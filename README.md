安装方式

```shell
pip install api4p4
```

使用方法

```python
from api4p4 import P4Client

p4_auth = {
    "port": "api4p4.com:1666",
    "user": "admin",
    "password": "admin",
}

p4 = P4Client(**p4_auth)
p4.set_workspace(
    workspace_name="admin_workspace",
    view=["//depot/test/... //admin_workspace/test/..."],
    options=["clobber"],
    root="D:\\workspace"
)
p4.login()
p4.update_all()
p4.disconnect()
```
