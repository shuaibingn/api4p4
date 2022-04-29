import re

from P4 import P4, P4Exception

from api4p4.decorator import check_connection
from api4p4.type_utils import type_detect_none


class P4Client:
    """P4  operation wrapper"""
    # The mode of add api4p4 mapping
    #                       w: overwrite
    #                       a: append write
    # DEFAULT_VIEW_MODE:    w: overwrite
    DEFAULT_VIEW_MODE = OVERWRITE_VIEW = "w"
    APPEND_VIEW = "a"
    VIEW_MODE = [OVERWRITE_VIEW, APPEND_VIEW]

    # Default version of sync
    DEFAULT_VERSION = "head"

    OPTIONS_LIST = ["allwrite", "clobber", "compress", "locked", "modtime", "rmdir"]
    P4_OPTIONS = "noallwrite noclobber nocompress unlocked nomodtime normdir"

    def __init__(self, logger=None, multiple=False, exception_level=1, **kwargs):
        """
        :param: multiple: invoke this prior to connecting if you need to use multiple P4 connections in parallel in a multi-threaded Python application.
        :param: port: api4p4 server, example api4p4.com:2002
        :param: user: user name
        :param: password: user password
        :param: charset: api4p4 character set, must be one of:
                none, auto, utf8, utf8-bom, iso8859-1, shiftjis, eucjp, iso8859-15,
                iso8859-5, macosroman, winansi, koi8-r, cp949, cp1251,
                utf16, utf16-nobom, utf16le, utf16le-bom, utf16be,
                utf16be-bom, utf32, utf32-nobom, utf32le, utf32le-bom, utf32be,
                cp936, cp950, cp850, cp858, cp1253, iso8859-7, utf32be-bom,
                cp852, cp1250, iso8859-2
        ...
        """
        self._workspace_name = ""
        self.password = kwargs.get("password")
        self.user = kwargs.get("user")

        self.p4 = P4(**kwargs)
        if multiple:
            self.p4.disable_tmp_cleanup()

        self.connect()
        if logger:
            self.p4.logger = logger

        self.p4.exception_level = exception_level

    @property
    def workspace(self):
        return self.p4.fetch_client(self._workspace_name)

    @property
    def workspace_name(self):
        assert self._workspace_name
        return self._workspace_name

    @property
    def workspace_view(self):
        return self.workspace.get("View", [])

    @check_connection
    def login(self, password=None):
        if password:
            self.password = password

        self.p4.run_login(password=self.password)

    def set_workspace(self, *args, **kwargs):
        """
        {
            "workspace_name":"test_workspace",
            "owner":"admin",
            "host":"xxx",
            "description":"Created by admin.\n",
            "root":"D:\\workspace",
            "options":[
                "clobber"
            ],
            "submit_options":"submitunchanged",
            "view":[
                "//depot/test/... //test_workspace/test/..."
            ]
        }
        """
        self.modify_workspace(*args, **kwargs)
        workspace_name = kwargs.get("workspace_name")
        self.switch_workspace(workspace_name)

    def workspace_exists(self, workspace_name):
        return self.p4.run_clients("-e", workspace_name)

    @staticmethod
    def _completion_view(workspace_name, view):
        """
        convert to complete mapping
        :return: the fully api4p4 view list
        """
        p4_view = []
        for x in view:
            if not x.startswith("//"):
                raise P4Exception(f"wrong format for p4_view")

            view_split_list_len = len(re.sub(re.compile(r"\s+", re.S), " ", x).split(" "))
            if view_split_list_len == 1:
                p4_view.append(f"{x} //{workspace_name}/{x[2:]}")
            elif view_split_list_len == 2:
                p4_view.append(x)
            else:
                raise P4Exception(f"invalid length of api4p4 view")

        return p4_view

    @check_connection
    def modify_workspace(self, workspace_name, owner=None, host=None, root=None, options=None,
                         submit_options="submitunchanged", view=None, mode=DEFAULT_VIEW_MODE):
        """
        :param workspace_name:
        :param owner:
        :param host:
        :param root:
        :param options:
        :param submit_options:
        :param view:
        :param mode: the mode of add api4p4 mapping
        """
        if mode not in self.VIEW_MODE:
            raise P4Exception(f"invalid mode of add api4p4 mapping: `{mode}`")

        options = options or []
        if not isinstance(options, list):
            raise P4Exception(f"parameter: `p4_options`, except `list`, got {type(options)}")

        for options in options:
            if options not in self.OPTIONS_LIST:
                raise P4Exception(f"invalid option for p4_options: `{options}`")

            self.P4_OPTIONS = re.sub(re.compile(rf"(un|no){options}", re.S), options, self.P4_OPTIONS)

        workspace = self.p4.fetch_client(workspace_name)
        if type_detect_none(owner):
            workspace["Owner"] = owner
        if type_detect_none(host):
            workspace["Host"] = host
        if type_detect_none(root):
            workspace["Root"] = root
        if type_detect_none(options):
            workspace["Options"] = self.P4_OPTIONS
        if type_detect_none(submit_options):
            workspace["SubmitOptions"] = submit_options
        if type_detect_none(view):
            if mode == self.OVERWRITE_VIEW:
                workspace["View"] = self._completion_view(workspace_name, view)

            elif mode == self.APPEND_VIEW:
                for add_view in view:
                    current_view_list = workspace.get("View") or []
                    if add_view not in current_view_list:
                        workspace["View"] = current_view_list + self._completion_view(workspace_name, view)

        self.p4.save_client(workspace)

    def switch_workspace(self, workspace_name):
        self.p4.fetch_client(workspace_name)
        self.p4.client = workspace_name
        self._workspace_name = workspace_name

    def add_view(self, workspace_name, view):
        self.modify_workspace(workspace_name=workspace_name, view=view, mode=self.APPEND_VIEW)

    @check_connection
    def update(self, file, version=None, force_sync=False):
        """
        update the specified version data from api4p4 server
        :param file: file to update
        :param version: specified version, default is latest(#head)
        :param force_sync:
        """
        if not version:
            version = self.DEFAULT_VERSION

        if version:
            version = version.lower()

        v = "#" + version
        if version != self.DEFAULT_VERSION:
            v = "@" + version

        file = f"{file}{v}"
        if not force_sync:
            self.p4.run_sync(file)
        else:
            self.p4.run_sync("-f", file)

    def update_all(self, version=None, force_sync=False, ergodic=False):
        if ergodic:
            for x in self.workspace_view:
                self.update(x.split(" ")[0], version, force_sync)

            return

        depots = set()
        for x in self.workspace_view:
            res = re.search(re.compile(r"^//[0-9a-zA-Z_\-]+/", re.S), x)
            if not res:
                raise P4Exception(f"invalid view {x}")

            depots.add(res.group().strip())

        for x in depots:
            self.update("{}...".format(x), version, force_sync)

    @check_connection
    def submit(self, msg):
        self.p4.run_submit("-d", msg)

    @check_connection
    def add(self, file: str):
        self.p4.run_add(file)

    @check_connection
    def edit(self, file: str):
        self.p4.run_edit(file)

    @check_connection
    def reconcile(self, params=None, file=None):
        """
        result = reconcile(["-d", "a"], "//depot/test.txt)
        """
        if not file:
            file = f"//{self.workspace_name}/..."

        params = params if params is not None else []
        params.append(file)

        return self.p4.run_reconcile(*params)

    @check_connection
    def delete_workspace(self, workspace_name):
        """delete workspace"""
        self.p4.run("client", "-d", workspace_name)

    @check_connection
    def get_changes(self, params=None):
        args = ["changes"]
        if params:
            args += params

        change = self.p4.run(*args)
        return change

    def get_latest_change(self, file=None, local=False):
        params = ["-m1"]
        if file:
            if local:
                file += "#have"
            params.append(file)

        change = self.get_changes(params)
        return change

    def connect(self):
        if not self.p4.connected():
            self.p4.connect()

    def disconnect(self):
        """disconnect from api4p4 server if is connected"""
        if self.p4.connected():
            self.p4.disconnect()
