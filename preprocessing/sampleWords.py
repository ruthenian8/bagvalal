"""Import word-annotation csv (first argument) and sample 100 random words"""
import asyncio
import aiofiles
import random
import sys

async def readFile(filename):
    async with aiofiles.open(filename, "r", encoding="utf-8") as f:
        contents = await f.read()
        return contents

async def writeLines(lines, filename):
    async with aiofiles.open(filename, "w+", encoding="utf-8") as f:
        await f.write("\n".join(lines))

async def main(filename):
    content = await readFile(filename)
    all_lines = content.splitlines()
    random.seed(42)
    chosen_lines = random.sample(all_lines, 100)
    await writeLines(chosen_lines, "chosen.csv")

if __name__ == "__main__":
    file = sys.argv[1]
    asyncio.run(main(file))