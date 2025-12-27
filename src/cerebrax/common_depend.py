# ----------------------- standard library ----------------------------
import asyncio, time, os, sys, typing, types, uuid, inspect, signal, shlex, tomllib, json
import pathlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
from importlib import util
from dataclasses import dataclass
from enum import Enum
import contextlib
from contextlib import asynccontextmanager
import collections
from collections import namedtuple
import platform, subprocess

# ----------------------- third-party library ----------------------------
import fastapi, uvicorn
from fastapi import (
    APIRouter,
    FastAPI,
    Request,
    Response,
    BackgroundTasks,
)
from uvicorn import Server, Config
import httpx, requests, aiohttp
from playwright.async_api import async_playwright
import aiofile, aiofiles, aiopath
from aiostream import stream
import psutil
import pydantic
from pydantic import (
    BaseModel,
    field_validator,
    ValidationError,
    ValidationInfo,
)
import watchdog
from watchdog.observers import Observer
from watchdog.events import (
    FileSystemEventHandler,
    PatternMatchingEventHandler,
    RegexMatchingEventHandler,
    LoggingEventHandler,
)
import lxml
from lxml import etree, html
import ijson
import bs4
from bs4 import BeautifulSoup

import redis
from redis import Redis
from redis.asyncio import Redis as AsyncRedis

import docker
from docker import errors
from docker.errors import ImageNotFound, APIError, DockerException


__all__ = [
    # standard library
    "asyncio", "time", "os", "sys", "typing", "types", "uuid", "inspect", "signal", "shlex", "tomllib", "json",
    "contextlib",
    "pathlib",
    "Path",
    "ThreadPoolExecutor", "as_completed", "ProcessPoolExecutor",
    "util",
    "dataclass",
    "Enum",
    "asynccontextmanager",
    "collections",
    "namedtuple",
    "platform", "subprocess",

    # third-party library
    "fastapi", "uvicorn",
    "APIRouter", "FastAPI", "Request", "Response", "BackgroundTasks",
    "Server", "Config",
    "httpx", "requests", "aiohttp",
    "async_playwright",
    "aiofile", "aiofiles", "aiopath",
    "stream",
    "psutil",
    "pydantic",
    "BaseModel", "field_validator", "ValidationError", "ValidationInfo",
    "watchdog",
    "Observer",
    "FileSystemEventHandler", "PatternMatchingEventHandler",
    "RegexMatchingEventHandler", "LoggingEventHandler",
    "lxml", "etree", "html",
    "ijson",
    "bs4", "BeautifulSoup",
    "redis", "Redis", "AsyncRedis",
    "docker", "errors", "ImageNotFound", "APIError", "DockerException",
]
