import setuptools

setuptools.setup(
    name="org_insight",
    version="1.0",
    author="炼器散人",
    author_email="dean-chen@qq.com",
    description="一个帮助操纵org table做数据分析的python库",
    long_description="支持dataframe和org table之间的转换，以及数据可视化",
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
