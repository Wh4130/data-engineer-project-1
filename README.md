# Taiwanese Media Analytics Pipelines and Dashboard
> In light of the absense of a database that stores Taiwanese news in a pool, I designed data pipeline and a streamlit UI to enhance the access to Taiwanese news data, especially for data scientists and NLP specialists. 
> This data engineering project automates and schedules the process of dynamic webscraping from three main media in Taiwan: CNA (中央社), UDN (聯合新聞網), and LTN (自由時報). 

📍Visit the dashboard [here](https://taiwan-media-dashboard-tool.streamlit.app/)!

## Technology
|Aspect | Technology |
| -- | -- |
| Language | Python |
| Web Scraping | Selenium, BeautifulSoup |
| Database | MongoDB ([MongoDB Atlas Database](https://www.mongodb.com/products/platform/atlas-database)) |
| Back-end (Pipeline) Cloud | [Render Cloud](https://render.com/) |
| User Interface | Streamlit | 
| Front-end Cloud | [Streamlit Cloud Platform](https://streamlit.io/) |

## Architecture 
```mermaid
flowchart LR
    
subgraph S ["Data Sources"]
    CNA
    LTN
    UDN

end

subgraph R ["Render (Cron@ 0 */2 * * *)"]
    P([Data pipelines])

    main[["scraping_cron.py"]]
    P -->|async run| main


    main -->|call| dbscript[["etl_tasks/mongodb.py"]]
    main -->|call| email[['utils/email_sender.py']]
end


CNA --> P 
UDN --> P
LTN --> P 

db[(MongoDB)]


email -->|send| admin((("Admin (Me)")))

subgraph MongoDB
    dbscript -->|load| db
end

subgraph Streamlit
    db --> utils
    utils(UI Utils) --> dashb[[dashboard.py]]
end

dashb --> U(((User)))

```
## User Interface
### Dashboard
#### Article Keyword Trends
![Article Keyword Trends](assets/ui_1.png)
#### Article Source and Type Distribution
![Article Source and Type Distribution](assets/ui_2.png)
#### Article Count by Type and Source
![Article Count by Type and Source](assets/ui_3.png)
#### Article Count by Time and Source
![Article Count by Time and Source](assets/ui_4.png)
#### Length Distribution
![Length Distribution](assets/ui_5.png)
#### Wordcloud
![Wordcloud](assets/ui_6.png)

### News Querying Tool
![News Querying Tool](assets/ui_7.png)

## Pipeline Design
### Batch Data Pipeline with Low Cost
> Utilizing the beginner plan on Render Cloud, the pipeline was deployed using the `cronjob` web service, which features a pay-as-you-go model. In my case, running the pipelines every two hours only takes me 1 USD per month.
> 
### Concurrent Scraping
> The data pipeline is designed to concurrently scrape news data from the three distinctive media webpages, which saves tremendous amount of time. 

### Dynamic Data Cleaning
> In order not to exceed the maximum storage amount of MongoDB Atlas free-tier, the pipelines delete news data prior to six months ago automatically. 

### Email Notification
> Email is sent to the admin (me) to notify the number of appened and removed news data in the database every time the pipeline is run. When the pipeline fails, email containing the error message is also sent to me.
![Notification Email](assets/etl_result_email_content.png)