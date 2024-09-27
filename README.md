# Node Projects Manager

A very simple GUI application to manage your Node.js projects.

<img width="705" alt="image" src="https://github.com/user-attachments/assets/1ebb6f84-f211-45ba-a8b2-c137b8984a88">

## Features

- **Start**, **stop**, and **restart** your Node.js projects from a graphical interface.
- Run `npm install` for individual projects directly from the GUI.
- Monitor output logs with color-coded messages for easy debugging.

## How to Use

### 1. Setup Configuration

- **Rename** `config.example.py` to `config.py` in the `project_manager` directory:

  ```bash
  mv config.example.py config.py
  ```

- **Edit** the `config.py` file to set your project configurations:

  ```python
  import os

  # Set the root directory to the parent directory of this file's directory
  root_dir = "./"

  # Define your list of Node.js projects
  project_list = ['project1', 'project2']
  ```

  - Ensure that `root_dir` correctly points to the directory containing your Node.js projects.
  - Update `project_list` with the names of your project directories.

### 2. Verify Directory Structure

Your directory should look like this:

```
root_directory/
├── project_manager/
│   ├── run.py          # The main script
│   └── config.py
├── project1/
│   └── index.js
└── project2/
    └── index.js
```

### 3. Run the Application

Navigate to the `project_manager` directory and run the script:

```bash
cd project_manager
python run.py
```

- Make sure you are in the `project_manager` directory when running the script.

### 4. Interact with the GUI

- **Start/Stop Projects**: Use the **Run** and **Stop** buttons next to each project to manage them individually.
- **Restart Projects**: Use the **Restart** button to restart a project.
- **npm Install**: Click **npm install** to install dependencies for a project.
- **Run All/Stop All**: Use the **Run All** and **Stop All** buttons to manage all projects at once.
- **View Logs**: Monitor the output logs in the scrollable text area at the bottom. Logs are color-coded:
  - **Black**: Standard output messages.
  - **Red**: Error or warning messages.

## Prerequisites

- **Python 3.x** installed on your system.
- **Tkinter** library for Python (usually included with Python).
- **Node.js** and **npm** installed on your system.
- Each Node.js project should have an `index.js` file as the entry point.

## Notes

- **Ensure Node.js and npm are installed** and accessible from your system's PATH.
- **Permissions**: Make sure you have the necessary permissions to execute scripts and access the project directories.
- **Python Libraries**: The script uses standard Python libraries. If you encounter issues with Tkinter, ensure it's installed correctly on your system.

## Troubleshooting

- **ModuleNotFoundError**: If you get an error about missing modules, ensure all Python dependencies are installed.
- **Permission Denied**: Check that you have execute permissions for the Node.js projects.
- **Incorrect Paths**: Verify that `root_dir` and `project_list` in `config.py` are set correctly.

## License

This project is open-source and available for modification and distribution.
