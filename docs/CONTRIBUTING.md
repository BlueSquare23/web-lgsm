# Contributing to Web-Lgsm

We welcome contributions to the web-lgsm project! By contributing, you help
make this project better for everyone. Here are some basic guidelines to get
you started.

## How to Help Out Most!

> [!TIP]
> Communication and collaboration is key!

While we do welcome novel feature ideas and requests, there is always a long
list of outstanding Todos for the project. If you're interested in contributing
to the project, please:

* [Checkout the existing Todos.md](https://github.com/BlueSquare23/web-lgsm/blob/master/Todos.md) file. (The one on the latest dev branch is most up-to-date!)
* [Checkout the latest dev branch](https://github.com/BlueSquare23/web-lgsm/branches) (both literally and figuratively)
* [Open a web-lgsm discussion](https://github.com/BlueSquare23/web-lgsm/discussions) saying you'd like to take something on
* [Get in touch directly](https://johnlradford.io/contact.php), I can help direct you to things that need worked on most

## A Note on LLM Usage

> [!IMPORTANT]
> NO GIANT AI GENERATED PRs PLEASE!

If I wanted to just let Claude or my own internal LLM's loose on this project I
know I could do that. But that's not the point of this project.

That's also not to say this project is totally anti AI, either. However, all AI
generated code must be fully vetted and understood by the human being
integrating it, and must comply with the existing style and architectural
patterns used in this project.

## How to Contribute

1. **Fork the Repository**
   - Fork the web-lgsm repository to your own GitHub account.

2. **Clone Your Fork**
   - Clone your forked repository to your local machine.
   - ```bash
     git clone https://github.com/your-username/web-lgsm.git
     ```

3. **Checkout the latest `dev-x.y.z` branch**
   - You can [view all current branches here](https://github.com/BlueSquare23/web-lgsm/branches)
   - ```bash
     git checkout dev-x.y.z  # For example dev-1.9.1
     git pull  # Just to be safe
     ```

4. **Create a new Branch off the Latest Dev Branch**
   - Create a new branch for your work.
   - ```bash
     git checkout -b my-feature-branch
     ```

5. **Make Your Changes**
   - Make your changes or additions in your branch.
   - If your changes are significant enough, please tweak test code accordingly
     &/or write new tests for you feature / tweak.

6. **Test Your Changes**
   - Run `--test_full` to ennsure your changes do not break
     anything and work as expected.

7. **Commit Your Changes**
   - Commit your changes with a clear and descriptive commit message.
   - ```bash
     git commit -m "Add feature XYZ does needful"
     ```

8. **Push Your Branch**
   - Push your branch to your forked repository.
   - ```bash
     git push origin my-feature-branch
     ```

9. **Create a Pull Request to the Latest Dev Branch**
   - To avoid conflicts run, `git fetch upstream` && `git merge upstream/dev-x.y.z` 
     before opening your pull request.
   - Open a pull request from your branch to the latest dev branchbranch of the web-lgsm
     repository.
   - You can [view all current branches here](https://github.com/BlueSquare23/web-lgsm/branches)
   - Provide a clear description of your changes and the problem they solve or
     the feature they add.

## Code Style

- Follow the existing code style and conventions in the project.
- Generally I'm following [Google's Python3 styleguide](https://google.github.io/styleguide/pyguide.html).
- Ensure your code is well commented, documented, tested.

## Reporting Issues

- If you find a bug or have a suggestion for improvement, please open an issue
  in the GitHub repository.
- Provide as much detail as possible, including steps to reproduce the issue if
  applicable.

## Code of Conduct

- By participating in this project, you agree to abide by the [Code of
  Conduct](CODE_OF_CONDUCT.md).

## Getting Help

- If you need help with your contribution, feel free to ask questions by
  opening an issue.

Thank you for your contributions!

