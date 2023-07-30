function say(word: string){
  console.log(word)
}

say("Hello from Typescript")

document.addEventListener("DOMContentLoaded", () =>{
  const paragraph = document.getElementById("tsdom") as HTMLParagraphElement
  paragraph.innerHTML = "This paragraph was set by typescript"
})
