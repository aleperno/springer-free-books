# springer-free-books
Python Script to download Springer Books

When ran the first time, the script will download a Excel file containing all
the available books. It will download ALL the books listed in the file, once it
downloads it, it prompts a message and waits for an ENTER.

If you with to download only a subset of books, you can edit the file before
resuming the execution.

If the script is ran again it will check if the catalog exists. For each of the
files to be downloaded, it also checks if they currently exist, if they do,
they aren't downloaded again.

The books will be downloaded to a 'downloads' folder, and the books will be
organized by folders for each of the categories.

## Requirements
Install requirements by

```
pip install -r requirements.txt
```

## Usage

```
python main.py
```

By default the script runs in a single thread, you can select the number of
threads by using the `-n` argument. By doing this, the script will download
multiple files at the same time, being the overall download faster.

```
python main.py -n 10
```
