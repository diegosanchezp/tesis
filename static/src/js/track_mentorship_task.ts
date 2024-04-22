/**
Makes sure that the we are working only with a dropzone element
*/
function isDropzone(element){
    return element.classList.contains("dropzone")
}

function isTask(element){
    return element.classList.contains("draggable-task")
}
document.addEventListener('DOMContentLoaded', () => {

    const draggableTasks = document.querySelectorAll(".draggable-task")

    // Define elements which can be dragged
    draggableTasks.forEach((draggableTask) => {
        draggableTask.addEventListener("dragstart", (event) => {
            // store the id of the dragged element
            event.dataTransfer.setData("text", event.target.id)

            // store the id of the dropzone that the dragged element is being
            // dragged from
        })
    })

    const dropzones = document.querySelectorAll(".dropzone")

    // https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/drop_event
    dropzones.forEach((dropzoneElement) => {

        dropzoneElement.addEventListener("dragover", (event) => {
            event.preventDefault()
        })

        dropzoneElement.addEventListener("dragenter", (event) => {

            const targetDropzone = event.target
            if(isDropzone(targetDropzone)){
                // Change border styles
                targetDropzone.classList.add("border-dashed")
            }

            if(isTask(targetDropzone)){
                // Change border styles
                targetDropzone.classList.add("border-ucv-blue")
            }
        })

        dropzoneElement.addEventListener("dragleave", (event) => {

            const targetDropzone = event.target

            if(isDropzone(targetDropzone)){
                // Change border styles
                targetDropzone.classList.remove("border-dashed")
            }
        })

        dropzoneElement.addEventListener("drop", (event) => {
            // prevent default action (open as a link for some elements)
            event.preventDefault();

            const draggableTaskId = event.dataTransfer.getData("text")
            const draggableTask = document.getElementById(draggableTaskId)
            const targetDropzone = event.target

            // We check if the target element is a dropzone, otherwise
            // tasks can be dropped inside other tasks elements
            if(isDropzone(event.target)){
                const taskOriginDropzone = draggableTask.parentNode

                // move dragged element to the selected drop target
                taskOriginDropzone.removeChild(draggableTask)
                targetDropzone.appendChild(draggableTask)
                targetDropzone.classList.remove("border-dashed")
            }
        })
    })

})
