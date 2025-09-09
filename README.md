# Ai-bash!
Console utility for integrating artificial intelligence into a Linux terminal. Allows you to ask an AI question and execute the scripts and commands suggested by the AI in the terminal. It will be useful for novice Linux administrators. 
  
The project is in the pre-alpha stage. In case of problems with the installation or operation of the Ai-bash utility, please contact me.

## Setup

### Ubuntu/Debian
Download `.deb` из [Releases](https://github.com/yourname/ai-bash/releases) and install:

```bash
sudo dpkg -i ai-bash_0.1.0-1_all.deb
sudo apt -f install  # it will tighten up the missing dependencies
```



### Run
```bash
ai [-run] Your request to the AI
```

### Example
```bash
ai Write a script in bash that outputs a list of files in the current directory.
```
or
```bash
ai -run Write a script in bash that outputs a list of files in the current directory.
```

## Remove
```bash
sudo apt remove ai-bash
```
