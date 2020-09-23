from setuptools import setup, find_packages

setup(
    name="mysql-stream",
    packages=find_packages(),
    version='0.0.2',
    description="simple and easy to use mysql client and ORM library",
    author="chenchong",
    author_email='boy3565@163.com',
    url="https://github.com/streamDream/mysqlstream",
    keywords=['mysql', 'client', 'orm'],
    classifiers=[],
    install_requires=[
        'DBUtils',
        'PyMySQL',
    ]
)
