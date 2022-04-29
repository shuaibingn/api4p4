from setuptools import setup, find_packages

with open("version", "r+", encoding="utf-8") as f:
    version = f.readline()
    version_list = version.split(".")
    if int(version_list[1]) >= 99:
        version_list[0] = str(int(version_list[0]) + 1)
        version_list[1] = "00"
    else:
        version_list[1] = str(int(version_list[1]) + 1)

    next_version = version_list[0] + "." + version_list[1]
    f.seek(0)
    f.write(next_version)

setup(
    name="api4p4",
    version=next_version,
    description=(
        "api for perforce"
    ),
    author="niushuaibing",
    author_email="niushuaibing@foxmail.com",
    maintainer="niushuaibing",
    maintainer_email="niushuaibing@foxmail.com",
    packages=find_packages(),
    platforms=["all"],
    url="",
    install_requires=[
        "p4python",
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3'
    ],
)
