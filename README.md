# Parvaah-Eldery-Care-Application

Parvaah One-Stop Application for Elderly Care

## Deployment

The application is hosted at [https://ridhim.pythonanywhere.com](https://ridhim.pythonanywhere.com).

## Requirements

Make sure you have the following installed:

- Python 3.6 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/Parvaah-Eldery-Care-Application.git
   cd Parvaah-Eldery-Care-Application
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:

   - On Windows:
     ```sh
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```sh
     source venv/bin/activate
     ```

4. Install the required libraries:
   ```sh
   pip install -r requirements.txt
   ```

## Configuration

1. Create a `.env` file in the `src` directory and add your environment variables (if any).

## Running the Application

1. Navigate to the `src` directory:

   ```sh
   cd src
   ```

2. Run the Flask application:

   ```sh
   python app.py
   ```

3. Open your web browser and go to `http://127.0.0.1:5000/` to see the application running.

## Stopping the Application

1. To stop the application, press `Ctrl+C` in the terminal.

2. You will be prompted to delete the `instance` and `__pycache__` folders. Follow the prompts to
   delete these folders if desired.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

