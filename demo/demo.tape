Output demo/demo.gif
Set Shell "bash"
Set FontSize 14
Set Width 900
Set Height 600
Set Theme "Catppuccin Mocha"
Set Padding 20

Hide
Type "export GITSTYLE_REPO_DIR=/path/to/gitstyle"
Enter
Type "cd $GITSTYLE_REPO_DIR"
Enter
Sleep 500ms
Type "cp demo/gitstyle-wrapper /tmp/gitstyle && chmod +x /tmp/gitstyle"
Enter
Sleep 300ms
Type "export PATH=/tmp:$PATH"
Enter
Sleep 300ms
Type "mkdir -p wiki/_meta wiki/languages && cp examples/edgarpavlovsky/*.md wiki/ && cp examples/edgarpavlovsky/_meta/*.md wiki/_meta/ && cp examples/edgarpavlovsky/languages/*.md wiki/languages/ 2>/dev/null"
Enter
Sleep 500ms
Type "clear"
Enter
Sleep 500ms
Show

Type "gitstyle version"
Sleep 500ms
Enter
Sleep 1s

Type "gitstyle run edgarpavlovsky"
Sleep 1s
Enter
Sleep 17s

Type "head -20 wiki/index.md"
Sleep 500ms
Enter
Sleep 3s
