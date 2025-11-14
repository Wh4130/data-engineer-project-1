import string
import smtplib
from dotenv import load_dotenv
import os
load_dotenv()

smtp_pw = os.getenv("SMTP_PASSWORD")

class EmailSender:

    @staticmethod
    def template(source, c_bef, c_aft, c_del):
        return f"""ETL process {source} results:
- count before ETL process:     {c_bef}
- count after ETL process:      {c_aft}
- count removed duplicated:     {c_del}
- count newly added documents:  {c_aft - c_bef}
"""
    @staticmethod
    def send(recipient_email, body):
        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.ehlo()
        smtp.starttls()
        smtp.login('huang0jin@gmail.com', smtp_pw)
        from_addr = 'huang0jin@gmail.com'
        to_addr = recipient_email
        msg = "Subject:[News Scraper] Result of daily scraping\n\n" + body
        status = smtp.sendmail(from_addr, to_addr, msg)#加密文件，避免私密信息被截取
        if status=={}:
            return "系統通知信已寄出"
        else:
            return "郵件傳送失敗!"
        smtp.quit()