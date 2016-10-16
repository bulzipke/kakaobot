try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from src import __version__

setup(name='kakaobot',
      version=__version__,

      packages=['kakaobot'],
      package_dir={'kakaobot': 'src'},

      install_requires=['aiohttp'],
      license='GNU General Public License version 3.0',
      author='bulzipke',
      author_email='bulzipke@naver.com',
      url='https://github.com/bulzipke/kakaobot',
      description='Python RESTFul server for Kakaotalk Bot API',
      keywords=['kakaotalk', 'bot'],
      classifiers=[
            'Development Status :: 1 - Planning',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Programming Language :: Python :: 3',
            'Topic :: Communications :: Chat',
            'Topic :: Software Development :: Libraries :: Python Modules'
      ])
