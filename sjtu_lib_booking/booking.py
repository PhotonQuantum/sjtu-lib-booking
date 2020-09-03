import re
from datetime import date, datetime
from typing import List, Optional

from httpx.exceptions import RedirectLoop
from lxml import html
from pysjtu import Client, Session

from .models import Reservation

HEADERS = {'Content-Type': 'application/x-www-form-urlencoded',
           'Host': 'booking.lib.sjtu.edu.cn',
           'Origin': 'http://booking.lib.sjtu.edu.cn',
           'Referer': 'http://booking.lib.sjtu.edu.cn/zg.asp',
           'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0'}
sn_pattern = re.compile("预约号:(?P<sn>.*)，可至")


class BookingManager:
    def __init__(self, username: str, password: str):
        self.session = Session(username, password)
        self.client = Client(self.session)

    def book(self, book_date: Optional[date] = None) -> Optional[int]:
        if not book_date:
            book_date = datetime.now().date()
        profile = self.client.profile
        payload = {'yuyuechangguan': '主馆',
                   'user_name': profile.name,
                   'xgh': profile.student_id,
                   'mobile': profile.cellphone,
                   'yuyueshijian': book_date.strftime("%Y-%m-%d"),
                   'chengnuo': 'on'}
        while True:
            try:
                r = self.session.post("http://booking.lib.sjtu.edu.cn/submit_zg.asp", headers=HEADERS, data=payload)
                break
            except RedirectLoop:
                pass
        sn = int(result.group("sn")) if (result := sn_pattern.search(r.text)) else None
        return sn

    def reservations(self) -> List[Reservation]:
        def tr_to_reservation(el: html.HtmlElement) -> Optional[Reservation]:
            tds: List[html.HtmlElement] = el.xpath(".//td")
            if len(tds) != 4:
                return None
            if tds[0].keys():
                return None
            return Reservation(int(tds[0].text), datetime.strptime(tds[2].text, "%Y-%m-%d").date())

        while True:
            try:
                r = self.session.get("http://booking.lib.sjtu.edu.cn/my2.asp")
                break
            except RedirectLoop:
                pass
        parsed_html = html.fromstring(r.text)
        trs = parsed_html.xpath("/html/body/main/section/div/div[2]/table[1]/tbody/tr")
        return list(filter(lambda x: x is not None, map(tr_to_reservation, trs)))
