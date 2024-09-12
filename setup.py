from distutils.core import setup

setup(
    name="cft-buoy-data-extractor",
    version="0.1.0",
    description="Client to extract buoy data from Centro Funzionale Toscana",
    author="Denny Baldini",
    author_email="dennybaldini@gmail.com",
    url="https://github.com/dennyb87/cft-buoy-data-extractor",
    install_requires=[
        "opencv-python==4.10.0.84",
        "plotdigitizer==0.3.0",
        "requests==2.31.0",
    ],
    packages=["cft_buoy_data_extractor"],
    package_dir={"": "src"},
)