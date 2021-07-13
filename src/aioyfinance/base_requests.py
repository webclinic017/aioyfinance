import asyncio

import aiohttp
import aiohttp.web as aioweb
from asyncio import Semaphore, Lock
import enum
from functools import partial
from random import uniform
import logging

PARALLEL = True #Allow overlapping of requests

if not PARALLEL:
    lock_ = Lock()
else:
    lock_ = None

MAX_BATCH = 5 #maximum requests active
semaphore_batch = Semaphore(MAX_BATCH)

PROXY_URL = None #set this parameter according to aiohttp documentation

MAX_RETRIES = 3 #amount of retries
if MAX_RETRIES <= 0:
    no_retries = True
else:
    no_retries = False

RETRY_DELAY = 1

MAX_RAND_DELAY = 0.5
MIN_RAND_DELAY = 0.1



class BaseRequest:
    @staticmethod
    async def get(url, is_json=False):

        await semaphore_batch.acquire()
        if not PARALLEL:
            await lock_.acquire()

        rand = uniform(MIN_RAND_DELAY, MAX_RAND_DELAY)
        await asyncio.sleep(rand)
        async with aiohttp.ClientSession() as session:

            if PROXY_URL is None:
                getter = partial(session.get, url)
            else:
                getter = partial(session.get, url, proxy=PROXY_URL)

            retries = MAX_RETRIES
            while retries or no_retries: #if retries > 0
                async with getter() as resp:
                    try:
                        if not is_json:
                            result = await resp.text()
                        else:
                            result = await resp.json()

                    except aioweb.HTTPError as e:
                        logging.error(url + ' ' + repr(e))
                        retries -= 1
                        if retries: #if > 0
                            await asyncio.sleep(RETRY_DELAY)
                        else:
                            result = None
                    else:
                        break

            semaphore_batch.release()
            if not PARALLEL:
                lock_.release()

            await asyncio.sleep(0) #next code is computational, let other requests finish
            return result


