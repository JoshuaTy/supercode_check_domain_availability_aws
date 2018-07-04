# Create a Bitbucket Repository

A [Supercode](http://gosupercode.com) function that creates a Bitbucket repository.

## Usage

```
import supercode

repo = supercode.call(
    "super-code-function",
    "your-supercode-api-key",
    username="john.doe@example.com",
    password="p@s$w0rd",
    team="ateam",
    repo_name="New Repo")

pprint(repo)
```

**Note:** Supercode has not been launched yet. This is for internal testing only.
