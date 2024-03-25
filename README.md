# Global Terrorism Perpetrators Dashboard

## Overview

The Global Terrorism Database (GTD), maintained by the University of 
Maryland, collects detailed data regarding terror events worldwide. The 
objective of this project is to build a focused and interactive data dashboard 
that conveys the key metrics surrounding the actions and behavioral 
evolution of terrorist groups. The target audience is media and public 
researchers who are interested in efficiently investigating the evolution and 
actions of terrorist perpetrators without the need to navigate the 
cumbersome GTD dataset themselves or scour other online sources to piece 
together a holistic understanding of a perpetrator group.

## Installation

1. **Install Docker Desktop**: 
   Ensure your local machine has Docker desktop installed. The dashboard is deployed via a docker container.

2. **Clone This Repository**: 
   Clone this repository to your local machine.

3. **Access the GTD dataset**: 
   Access the GTD dataset and obtain a license (https://www.start.umd.edu/gtd/).

4. **Transform the data**: 
   Open `ETL.py` and replace `gtd_fpath` with the relative or absolute path to the `globalterrorismdb_0522dist.xlsx` you downloaded from the GTD website.

5. **Build the Docker Image**: 
   The raw dataset has been transformed and is now placed in the `DashboardCode` repository. Now, we will build the docker container, launch it, and visit the dashboard.

   ```bash
   cd <absolute path to TerrorDashboard/DashboardCode>
   docker build -t terrordashboard .
   docker run -h localhost -p 8051:8050 -d --name tdb terrordashboard
   docker ps -a #or go to docker desktop to see the container running on: http://localhost:8051
   ```

## Usage

Once the docker container is deployed, the web dashboard application can be visited in the web browser. Data pertaining to notable terror groups can be explored via the interactive Plotly visualizations.

## Contributing

Contributions are not being accepted at this time.

## License

This project is licensed under the [MIT License](LICENSE). See the [LICENSE](LICENSE) file for details.
