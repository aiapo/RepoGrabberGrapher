# RepoGrabberGrapher
This tool is designed to help dynamically visualize statistics from a provided dataset generated by the tool '[RepoGrabber](https://github.com/aiapo/RepoGrabber).'

It takes input of two CSVs; the refactorings and repository datasets, or alternatively a SQL connection that uses the tables RepoGrabber generated.

It then spins up a local web server located at port 8000 where you can interact with the dataset dynamically.

# Running
### Install dependencies
```bash
pip install -r requirements.txt
```

### Run
```bash
python main.py --repositorycsv YOUR_REPOSITORY_CSV --refactoringcsv YOUR_REFACTORING_CSV
```

Where *YOUR_REPOSITORY_CSV* and *YOUR_REFACTORING_CSV* are the CSVs exported from RepoGrabber for repository and refactoring information respectively.

You also may use HTTP directly, but be aware on large datasets this can be slow/undesired. Planning to locally download the CSV if this is choosen, but it's not implemented.

### Open
The webpage should open automatically in your default browser, but it is located at localhost:8000 as well.

# Todo
* More statistics
* SQL intergration
* Additional filters
* Download CSVs locally if they are from a remote source
* Speedups