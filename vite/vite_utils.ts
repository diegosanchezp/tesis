import { readdirSync } from 'node:fs';
import { resolve } from "path";

/** Get the input files of a particular folder */
function getInputFiles(dir_path: string): string[]{

  const files = readdirSync(dir_path, {withFileTypes: true})

  // this array contains the string version of the full path
  // of the files that we want to bundle
  const filesStr: string[] = []

  // Ignore these files, we don't want to bundle them
  const ignore = [
    'step_view_logic.ts'
  ];

  for (const file of files){
    // We only want the files of this directory
    // not its sub-folders
    if (!file.isDirectory() && !ignore.includes(file.name))
      filesStr.push(resolve(`${dir_path}/${file.name}`))
  }

  return filesStr

}

export {getInputFiles}
// Uncomment to test the functions
// const filesStr = getInputFiles(resolve("../static/src/js"))
// console.log(filesStr)
