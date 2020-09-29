# Welcome to MAIRDISY (MAIR DIalog SYstem).

The project consists in designing, implementing, evaluating and writing about a restaurant recommendations dialog system using various methods from AI, such as domain modeling, text classification using machine learning and user experience testing. The dialog system is programmed in Python 3. The program is terminal/command line based. No graphical user interface was used. 

The project is divided into two parts: 

- The first part of the project concerns the implementation of the dialog system: modeling the domain in a dialog model, and implementing and evaluating a machine learning classifier for natural language. 
- The second part of the project is about evaluating your system: designing, carrying out and reporting on user experiments, as well as thinking about your system in the wider context of AI.

## How to install and run
### Required libraries
MAIRDISY is written in Python 3 and it utilises various libraries:
> Be sure all the following libraries are installed

```shell
pip install numpy
pip install nltk
pip install python-Levenshtein
pip install scikit-learn
pip install pandas
pip install argparse
```
### Run MAIRDISY - Console
After downloading and extracting the .zip file containing the files in this repository, 
extract those. In that new folder there are all the classes containg MAIRDISY.

> Enter to the project folder and run main.py
>
```shell
python3 -m unittest src/main.py 
```

### Run MAIRDISY - Importing from version control
Using an IDE, you can import the project from version control, using: `https://github.com/BeppeMarnell/TeamProjectMAIR`


### Configurable parameters
> For formal language, add the following in the main method 
```shell
p = argparse.ArgumentParser()
p.add_argument("--formal", help="formal or informal system speach. Use informal for informal "speech.", default="formal")
args = p.parse_args(sys.argv[1:])
Main(args.formal, args.delay, args.caps)
```

> For system delay, add the following in the main method
```shell
p = argparse.ArgumentParser()
p.add_argument("--delay", help="Use delay for a delay of 2 seconds. Use mess_delay for a delay of 2 seconds "accompanied with a message. Use off for no delay", default="off")
Main(args.formal, args.delay, args.caps)
```

> For System with all CAPS, add the following in the main method
```shell
p = argparse.ArgumentParser()
p.add_argument("--caps", help="Use caps for system output to be in all caps.", default="no_caps")
args = p.parse_args(sys.argv[1:])
Main(args.formal, args.delay, args.caps)
```



<!-- # Transition diagram:
![Image of Yaktocat](diagram.jpg) -->


