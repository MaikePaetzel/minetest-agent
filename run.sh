# run minetest server

MINETEST_WORLDNAME=flatland
MINETEST=../../software/minetest/bin/minetest
PATH_TO_NPCF=agent/npcf+miney/npcf
PATH_TO_NPCFEY=agent/npcf+miney/npcfey

cp -R $PATH_TO_NPCF /home/nrg/software/minetest/mods
cp -R $PATH_TO_NPCFEY /home/nrg/software/minetest/mods
$MINETEST --server --worldname $MINETEST_WORLDNAME
$MINETEST --go --name Minehart --address localhost --port 30000