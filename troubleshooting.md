# Troubleshooting
Troubleshooting steps and knowledge for different parts of the software and Sentry

## Database problems
Don't use a sqlalchemy or pg8000 that is higher than sqlalchemy==1.3.15, pg8000==1.12.5, or things will fail.

If you're running the app locally and the database queries are failing, here are some things to check:

Did you remember to permit / whitelist your IP address as an 'Authorized Network' in CloudSQL?

Did any of the Connection Info for the CloudSQL instance change? Go to  CLoudSQL Settings -> Connection Info and check HOST and other details from the .env files.

Did the GCP documentation change? For connecting via Unix socket vs TCP, regarding the recommended libraries and implementations to use.

When was this last run successfully? Check past closed PR's.

Did you try all of the interchangeable backends Python, Java, Node? Or is only 1 of them failing?

## Releases
Q. `--update-env-vars` is not available for `gcloud app deploy`, therefore can't pass a RELEASE upon deploying. Luckily it's already built into the /build which gets uploaded, and sentry-cli generated it, as well as the RELEASE that sentry-cli uses for uploading source maps.

A. So, creating the dynamic Release inside of main.py. Hard-coding it into .env wouldn't help, as it needs to be dynamic. This release may not match what sentry-cli is generating for release (due to clock skew), but we're not uploading source maps for python. Worst case, the Python release is slightly different than the React release, but this shouldn't matter, because two separate apps (repo) typically have unique app version numbers anyways (you version them separately).

## Python
'default' is a function applied to objects that aren't serializable.  
use 'default' or else you get "Object of type datetime is not JSON serializable":  
json.dumps(results, default=str)  


## React
https://dev.to/brad_beggs/handling-react-form-submit-with-redirect-async-await-for-the-beyond-beginner-57of

https://www.pluralsight.com/guides/how-to-transition-to-another-route-on-successful-async-redux-action

https://reactjs.org/docs/forms.html

State Hooks vs Effect Hooks vs Context
https://reactjs.org/docs/hooks-state.html

Context
https://reactjs.org/docs/hooks-effect.html

https://docs.sentry.io/platforms/python/guides/flask/configuration/filtering/#using-sampling-to-filter-transaction-events

## Git
If `git pull` is hanging or `sudo git pull` is giving you
```
Warning: Permanently added the ECDSA host key for IP address '140.82.114.3' to the list of known hosts.
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.

Please make sure you have the correct access rights
and the repository exists.
```
Then create a new SSH key and upload it to github.

Step1
https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent

Step2
https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account

```
ssh-keygen -t ed25519 -C "your_email@example.com"
eval "$(ssh-agent -s)"
ssh-add -K ~/.ssh/id_ed25519

cat ~/.ssh/id_ed25519.pub
copy it
Github > User Settings > SSH and GPG Keys > New SSH Key > paste
```

But don't follow the step about editing the `~/.ssh/config` file.

`ssh-add -K ~/.ssh/id_ed25519` may need to be run as `ssh-add ~/.ssh/id_ed25519`