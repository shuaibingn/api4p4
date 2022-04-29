import logging
import logging.handlers

from api4p4.p4 import P4


class LoggerHandler(logging.Logger):

    def __init__(self, name='root', level=logging.INFO, fm=None):
        super().__init__(name)

        self.setLevel(level)
        fmt = logging.Formatter(fm)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level)
        stream_handler.setFormatter(fmt)
        self.addHandler(stream_handler)


logger = LoggerHandler(
    name="dgm",
    level=logging.INFO,
    fm='%(asctime)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s'
)

if __name__ == '__main__':
    p4_auth = {
        "port": "api4p4.com:1666",
        "user": "admin",
        "password": "admin",
    }

    p4 = P4(**p4_auth)
    p4.login()
    p4.set_workspace(
        workspace_name="admin_workspace",
        view=["//depot/test/... //admin_workspace/test/..."],
        host="",
        options=[],
        root="D:\\workspace"
    )
    print(p4.workspace)
    print(p4.workspace_name)
    print(p4.workspace_view)

    p4.modify_workspace(workspace_name=p4.workspace_name, view=["//depot/test/... //admin_workspace/test/test/..."])
    print(p4.workspace)
    print(p4.workspace_name)
    print(p4.workspace_view)

    p4.switch_workspace("another_test")
    print(p4.workspace)
    print(p4.workspace_name)
    print(p4.workspace_view)

    p4.disconnect()
