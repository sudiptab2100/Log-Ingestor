# Log Ingestor & Query Interface

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

![Web Interface](https://i.imgur.com/1gIxRD7.png)

It project inlcudes a log ingestor which consumes log data on port 3000. And it has an easy to use web interface to query, search and filter data.

Features:
* It can scale and consume vast amount of log data. It uses Kafka for this purpose.
* Used MongoDB as database.
* It can do full-text search on the field 'message'.
* It can apply nested filters in search.
* It can search data within a range of date (timestamp).
* It has real-time log ingestion & search results.

### Built With

* Apache Kafka
* MongoDB
* Python
* Postman
* WSL (Ubuntu)

<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

This project requires Python 3.8, Python Virtual Environment Module, Apache Kafka, MongoDB to be pre-installed.

### Installation

_Instructions for projct setup._

```sh
git clone https://github.com/dyte-submissions/november-2023-hiring-sudiptab2100.git
cd november-2023-hiring-sudiptab2100/src
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

<!-- USAGE EXAMPLES -->
## Usage

Be in the `src` directory and run the following commands

* Run `Log Ingestor Server` 

  ```sh
  python app.py
  ```
* Run `Web Interface Server` 

  ```sh
  python ui.py
  ```

New logs can ingested to the server on port 3000 using the following `cURL` command:
  ```sh
  curl --location 'http://127.0.0.1:3000/' \
  --header 'Content-Type: application/json' \
  --data '{
    "level": "error",
    "message": "Succeed to connect to DB",
      "resourceId": "server-1234",
    "timestamp": "2023-09-15T08:00:00Z",
    "traceId": "abc-xyz-123",
      "spanId": "span-456",
      "commit": "5e5342f",
      "metadata": {
          "parentResourceId": "server-0987"
      }
  }'
  ```



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<!-- CONTACT -->
## Contact

Sudipta Basak - [@sudipta__basak](https://twitter.com/sudipta__basak) - sudiptab2100@gmail.com

Project Link: [https://github.com/dyte-submissions/november-2023-hiring-sudiptab2100](https://github.com/dyte-submissions/november-2023-hiring-sudiptab2100)
