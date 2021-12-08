import sys
from subprocess import Popen, PIPE

import asyncio
import schedule

import actions.gnome

import logging
logging.basicConfig(level=logging.INFO)
logging.raiseExceptions = False


# https://stackoverflow.com/a/1091428
async def check_found(pid):
    process = Popen(['ps', '-p', pid], stdout=PIPE, stderr=PIPE)
    stdout, _ = process.communicate()
    logging.info(stdout)
    return len(stdout.splitlines()) > 1


async def run_continuously():
    # Initial check
    pid = sys.argv[1]
    name = sys.argv[2]

    found = await check_found(pid)
    if not found:
        logging.info("The process is not found")
        sys.exit(0)

    # Scheduled checks
    async def check_and_update():
        global found
        found = await check_found(pid)

    task = asyncio.create_task(check_and_update())

    def create_task():
        global task
        task = asyncio.create_task(check_and_update())

    schedule.every().minutes.do(create_task).tag("default")

    while found:
        schedule.run_pending()
        await asyncio.gather(
            task,
            asyncio.sleep(0.5)
        )
    
    logging.info("Taking actions for the terminated process")
    await actions.gnome.alert_terminated(pid, name)

if __name__ == "__main__":
    asyncio.run(run_continuously())
