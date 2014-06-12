hivedir=`python -c 'import sys,os;print os.path.split(os.path.abspath(sys.argv[0]))[0]' $0`
cd $1/scripts/addons || { echo $1 'has no "scripts/addons" dir' ; exit 1; }
rm -rf hive
mkdir hive
cp -r $hivedir/libcontext hive
cp -r $hivedir/bee hive
cp -r $hivedir/dragonfly hive
cp -r $hivedir/hiveguilib hive
cp -r $hivedir/gui/blenderproject hive
cp -r ~/data/Spyder/spyder hive
rm -rf hive/spyder/.bzr
rm -rf hive/spyder/WISDOM
cd hive
rm -rf spyder/tempdir
mkdir spyder/tempdir
\cp ~/data/Spyder/wisdom.py .
python wisdom.py spyder
\cp ~/data/Spyder/wisdom-blender.py __init__.py
../../../../blender --factory-startup -b -y -P $hivedir/test-addon.py
\cp $hivedir/wisdom-blender.py __init__.py
rm -rf bee/hivemap/spycache
rm -rf bee/hivemap/WISDOM
../../../../blender --factory-startup -b -y -P $hivedir/test-addon.py
\cp $hivedir/gui/blendergui.py __init__.py
\cp $hivedir/gui/locations.conf .
cd ..
rm -f $hivedir-dist/hive-addon.zip
zip -r $hivedir-dist/hive-addon.zip hive