from setuptools import setup, find_packages

setup(
    name="video-to-gif-bot",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "python-telegram-bot>=20.0",
        "moviepy==1.0.3",
        "Pillow==9.5.0",
        "decorator>=4.0.2",
        "imageio>=2.5",
        "imageio-ffmpeg>=0.4.4",
        "tqdm>=4.11.2",
        "numpy",
        "requests>=2.25.0",
        "python-magic>=0.4.24",
    ],
    python_requires=">=3.8",
) 
