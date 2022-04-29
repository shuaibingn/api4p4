## Install

```shell
pip install api4p4
```

## Use

```python
from api4p4.p4 import P4

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
    options=["clobber"],
    root="D:\\workspace"
)
p4.update_all()
p4.disconnect()
```

## example

[p4_client_example](./examples/p4_example.py)

LICENSE

[Apache 2.0](./LICENSE)