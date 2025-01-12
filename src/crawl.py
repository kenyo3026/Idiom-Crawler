import os
import asyncio
import aiohttp
import aiofiles
import backoff
from tqdm import tqdm


timeout = aiohttp.ClientTimeout(total=30) 


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

MAX_EXHAUSTIVE_ID = 10000
MAX_CONCURRENT_NUMS = 50

MAX_TRIES = 3
MAX_TIME = 60

URL_TEMPLATE = "https://dict.idioms.moe.edu.tw/bookView.jsp?ID={id}"
OUTPUT_ROOT = "../output"
OUTPUT_HTML_ROOT = f"{OUTPUT_ROOT}/html"


@backoff.on_exception(
   backoff.expo,        # Exponential backoff strategy
   (aiohttp.ClientError, asyncio.TimeoutError),  # Exceptions that trigger retry
   max_tries=MAX_TRIES, # Maximum number of retry attempts
   max_time=MAX_TIME,   # Maximum total time in seconds to retry
)
async def get_html(session, url, output_path, headers:dict=HEADERS):
    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                html_content = await response.text()
                
                if output_path:
                    root, _ = os.path.split(output_path)
                    if root and not os.path.exists(root):
                        os.makedirs(root, exist_ok=True)
                    
                    async with aiofiles.open(output_path, "w", encoding="utf-8") as file:
                        await file.write(html_content)

                # print(f"Successfully downloaded HTML for {url}.")
                return html_content
            else:
                print(f"Failed to download HTML for ID {url}. Status code: {response.status}")
                return None

    except Exception as e:
        print(f"Error processing ID {url}: {str(e)}")
        return None


async def main():
    
    async with aiohttp.ClientSession() as session:

        tasks = []
        OUTPUT_HTML_ROOT = f"{OUTPUT_ROOT}/html"

        for _id in range(MAX_EXHAUSTIVE_ID):

            url = URL_TEMPLATE.format(id=_id)
            output_html_path = f"{OUTPUT_HTML_ROOT}/bookView_{_id}.html"

            task = get_html(session, url, output_html_path)
            tasks.append(task)

        # for i in range(0, len(tasks), MAX_CONCURRENT_NUMS):
        for i in tqdm(range(0, len(tasks), MAX_CONCURRENT_NUMS), desc="Processing chunks"):
            chunk = tasks[i:i + MAX_CONCURRENT_NUMS]
            await asyncio.gather(*chunk)


if __name__ == "__main__":
    asyncio.run(main())