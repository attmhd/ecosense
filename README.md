
# Ecosense

This project is final project for Embedded System Course called Ecosense for monitoring temperature and humidity and some prediction.
## Tech Stack

[![My Skills](https://skillicons.dev/icons?i=mysql,fastapi,tensorflow,arduino)](https://skillicons.dev)

## Authors

- [@attmhd](https://github.com/attnmhd/)

## Prerequisites

Before you begin, make sure you have Python 3.12 > on your local machine.

## Installation

Follow these steps to get the project running on your local machine.

### Step 1: Clone the Repository

Clone the project repository to your local machine:

```bash
git clone https://github.com/attmhd/ecosense.git
cd ecosense
```

### Step 2: Setup Environment Variables
Create a **.env** file in the root of your project directory and add the following database configuration:
```env
DB_HOST=your_host
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_NAME=your_database_name

```

### Step 3: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
go pip install -r requirements.txt
```

### Step 5: Training Model

```bash
./training.sh
```

### Step 6: Running the Application

Run Server

```bash
uvicorn server:app --host {your_host} --port {your_port}
```

Run Streamlit
```bash
streamlit run dashboard/main.py
```
