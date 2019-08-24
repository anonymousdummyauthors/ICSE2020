# Haskell Dockerfile Linter Installation Guide in Ubuntu/Debian
1. Install Stack tool

	`curl -sSL https://get.haskellstack.org/ | sh`

2. Build the linter

	`git clone https://github.com/hadolint/hadolint`

	`cd hadolint`

	`stack install`

3. Copy the generated executable file to `/usr/local/bin`