# Langchain Data Analysis Tool

A Flask-based web application that allows users to perform exploratory data analysis (EDA) on uploaded datasets. The application facilitates various data analysis techniques and visualizations, providing insights into the underlying patterns and statistics of the data.

## Features

- File upload system for CSV datasets.
- Data description and dataset definition via the web interface.
- Perform multiple EDA operations, including:
  - Handling missing values.
  - Generating statistical summaries.
  - Creating various plots and visualizations.
- Extensible architecture for adding new EDA methods.

## Installation

To set up the project locally, follow these steps:

1. Clone the repository:

    ```bash
    git clone https://github.com/hritvikgupta/langchain-data-analysis-tool.git
    cd langchain-data-analysis-tool
    ```

2. Create a virtual environment (optional):

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the requirements:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up environment variables by creating a `.env` file with the necessary API keys:

    ```plaintext
    OPENAI_API_KEY=your_openai_api_key
    E2B_API_KEY=your_e2b_api_key
    ```

5. Run the Flask application:

    ```bash
    flask run
    ```

## Usage

After starting the application, navigate to `http://localhost:5000/` in your web browser to access the tool. Upload a CSV file and use the web interface to perform data analysis operations.

## Contributing

Contributions are welcome! If you have suggestions or want to contribute to the project, feel free to create issues or pull requests on the GitHub repository.

## License

[MIT License](LICENSE) - see the `LICENSE` file for details.


## Run this using Docker and Docker Command to use when you have to pull the image and edit it
1. First pull the image
    ```bash
    docker pull hritvik7654/edaimage:updated
     ```
2. create container for the pulled image
    ```bash
    docker create —name Eda-temp hritvik7654.edaimge:latest
     ```
3. Copy the contents of docker images to local repository to edit
    ```bash
    docker cp eda-temp:/app /Users/aayush-gupta/Downloads/edaimage
     ```
    if want to copy any specific file in current working directory
    ```bash
    docker cp temp:/app/templates/define_dataset.html .
     ```
4. code . to open up the repo on vs code
5. make changes in the code then build the image with new tag
    ```bash
    docker build -t hritvik7654/edaimage:02 .
     ```
6. Run the image with environment variables
    ```bash
    docker run —d -p 5001:5000 -e OPENAI_API_KEY = “” -e E2B_API_KEY=”” hritvik7654/edaimage:02
    ```
8. First request to add you as a collaborator and then push otherwise push will be rejected
    Request access on hritvik7654@gmail.com
    
9. If image is running successful then push the image
```bash
   docker push hritvik7654/edaimage:02
    ```
