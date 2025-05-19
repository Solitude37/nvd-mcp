from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("nvd")

# Constants
NWS_API_BASE = "https://services.nvd.nist.gov/rest/json/cves/2.0"
USER_AGENT = "nvd-app/1.0"

async def make_request(url: str, params: dict[str, Any]) -> dict[str, Any] | None:
    """Make a request to the API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(e)
            return None

@mcp.tool()
async def get_cve_details(cve_id: str) -> Any:
    '''
    Fetch the details of a CVE.
    
    Returns the raw JSON, or an error message if the fetch fails.
    '''
    url = f"{NWS_API_BASE}"
    params = {"cveId": cve_id}
    response = await make_request(url, params)
    if response is None:
        raise ValueError(f"Error fetching CVE details")
    
    result = []

    datalist = response['vulnerabilities']

    cve_id = datalist[0]['cve']['id']
    cve_description = datalist[0]['cve']['descriptions'][0]['value']
    cve_score = datalist[0]['cve']['metrics']['cvssMetricV31'][0]['cvssData']['baseScore']
    references = datalist[0]['cve']['references']

    result.append({
        "id": cve_id,
        "description": cve_description,
        "score": cve_score,
        "references": references
    })
    
    return result

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')