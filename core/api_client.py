import httpx
from core.config import API_BASE_URL

def get_merch_stock(item_name: str):
    response = httpx.get(f"{API_BASE_URL}/merchandise")
    data = response.json()
    for item in data.get("merchandise", []):
        if item["name"].lower() == item_name.lower():
            return item["stock"]
    return None

def get_jadwal_terdekat():
    response = httpx.get(f"{API_BASE_URL}/jadwal/terdekat")
    data = response.json()
    return data.get("jadwal")

def get_jadwal_by_lawan(nama_lawan: str):
    response = httpx.get(f"{API_BASE_URL}/jadwal", params={"lawan": nama_lawan})
    data = response.json()
    return data.get("jadwal")

def get_pemain_by_nama(nama: str):
    response = httpx.get(f"{API_BASE_URL}/pemain", params={"nama": nama})
    data = response.json()
    pemain_list = data.get("pemain", [])
    return pemain_list[0] if pemain_list else None

def get_pemain_by_posisi(posisi: str):
    response = httpx.get(f"{API_BASE_URL}/pemain", params={"posisi": posisi})
    return response.json().get("pemain", [])

def get_pemain_by_status(status: str):
    response = httpx.get(f"{API_BASE_URL}/pemain", params={"status": status})
    return response.json().get("pemain", [])

def semantic_search_api(query: str, top_k: int = 3):
    response = httpx.post(
        f"{API_BASE_URL}/search/semantic",
        json={"query": query, "top_k": top_k}
    )
    return response.json().get("results", [])