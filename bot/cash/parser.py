import requests
import json

tournaments_completed = 'https://na.wotblitz.com/ru/api/tournaments/?page=1&page_size=10&order_by[]=tags&order_by[]=-start_at&phase_group=completed'
tournaments_planned = 'https://na.wotblitz.com/ru/api/tournaments/?page=1&page_size=10&order_by[]=tags&order_by[' \
                      ']=-start_at&phase_group=planned'
tournaments_active = 'https://na.wotblitz.com/ru/api/tournaments/?page=1&page_size=10&order_by[]=tags&order_by[' \
                     ']=-start_at&phase_group=active'

headers_arg = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0"
}


class WotBlitzTournaments:
    def get_active_tournaments(self):
        return self.get_tournaments(tournaments_active)

    def get_planned_tournaments(self):
        return self.get_tournaments(tournaments_planned)

    def get_completed_tournaments(self):
        return self.get_tournaments(tournaments_completed)

    @staticmethod
    def get_tournaments(url):
        result = []
        print(json.loads(requests.get(url, headers=headers_arg).text)["results"][0]["description"]["title"])
        for i in json.loads(requests.get(url, headers=headers_arg).text)["results"]:
            max_prize = ""
            for el in i["prizes"]:
                if el["type"] == "credits":
                    max_prize = str(el["count"])
            result.append({"title": i["description"]["title"],
                           "start_at": i["start_at"],
                           "end_at": i["end_at"],
                           "img": i["files"]["logo_preview"],
                           "id": i["id"],
                           "max_prize": max_prize})
        return result
