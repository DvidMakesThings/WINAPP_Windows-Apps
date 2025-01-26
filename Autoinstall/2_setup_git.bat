@echo off
echo ============================================
echo Configuring Git
echo ============================================
git config --global user.name DvidMakesThings
git config --global user.email s.dvid@hotmail.com
git config --global core.editor notepad
git config --global init.defaultBranch master

echo Generating a global Git ignore file...
echo node_modules  %USERPROFILE%.gitignore_global
echo .env  %USERPROFILE%.gitignore_global
git config --global core.excludesfile %USERPROFILE%.gitignore_global

echo ============================================
echo Git has been configured!
echo ============================================
pause
