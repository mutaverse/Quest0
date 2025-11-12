from tavily import TavilyClient
from dotenv import load_dotenv
import os
load_dotenv('.env')


def tavily_search_tool(
        query: str, max_results: int = 5, include_images: bool = False
        ) -> list[dict]:
    """
    Performs a search using Tavily API.

    Args:
        query (str): The search query.
        max_results (int): The number of results to return (default 5)
        include_images (bool): Whether to include images in search results (default false).

    Returns:
        list[dict]: A list of dictionaries with keys like "title", 'content' and 'url'
    """

    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY not found in environment variables.")

    # Define the Tavily client (instantiate it)
    client = TavilyClient(api_key=api_key)

    try:
        response = client.search(
            query=query, max_results=max_results, include_images=include_images
        )

        results = []
        for r in response.get('results', []):
            results.append(
                {
                    "title": r.get("title", ""),
                    "content": r.get("content", ""),
                    "url": r.get("url", "")
                }
            )
        
        if include_images:
            for img_url in response.get("images", []):
                results.append({"image_url": img_url})
        
        return results
    except Exception as e:
        return [{"error": str(e)}]
