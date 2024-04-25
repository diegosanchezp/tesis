import { getCSRFToken } from "js/utils/index"
/**
Makes sure that the we are working only with a dropzone element
*/
function isDropzone(element){
    return element.classList.contains("dropzone")
}

function isTask(element){
    return element.classList.contains("draggable-task")
}

const DRAGENTER_BORDER_STYLE = "border-dashed"
const DEFAULT_COL_BORDER_STYLE = "border-solid"

function setTaskNumString(taskNumElement: HTMLElement, taskNumTextElement: HTMLElement, action: string){
    let taskNum = parseInt(taskNumElement.innerHTML)

    if(action === "increment"){
        taskNum += 1
    }
    if(action === "decrement"){
        taskNum -= 1
    }

    taskNumElement.innerHTML = taskNum

    if(taskNum >= 2 || taskNum === 0){
        taskNumTextElement.innerHTML = "tareas"
    } else {
        taskNumTextElement.innerHTML = "tarea"
    }

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
                targetDropzone.classList.remove(DEFAULT_COL_BORDER_STYLE)
                targetDropzone.classList.add(DRAGENTER_BORDER_STYLE)
            }

            if(isTask(targetDropzone)){
                // Change border styles
                targetDropzone.classList.add("border-ucv-blue")
            }
        })

        dropzoneElement.addEventListener("dragleave", (event) => {

            const targetDropzone = event.target

            if(isDropzone(targetDropzone)){
                // Restore border styles to default
                targetDropzone.classList.remove(DRAGENTER_BORDER_STYLE)
                targetDropzone.classList.add(DEFAULT_COL_BORDER_STYLE)
            }
        })

        dropzoneElement.addEventListener("drop", async (event) => {
            // prevent default action (open as a link for some elements)
            event.preventDefault();


            // We check if the target element is a dropzone, otherwise
            // tasks can be dropped inside other tasks elements
            if(isDropzone(event.target)){
                const taskGroupIdPrefix = "task-group-"

                const draggableTaskId: string = event.dataTransfer.getData("text")
                const draggableTask = document.getElementById(draggableTaskId)

                const targetDropzone = event.target
                const targetDropzoneId = targetDropzone.getAttribute('id')
                const targetDropzoneTaskContainer = targetDropzone.querySelector(
                    `#${taskGroupIdPrefix}${targetDropzoneId}`
                )
                const targetDropzonetaskNumElement = targetDropzone.querySelector(
                    `#${targetDropzoneId}-task-num`
                )
                const targetDropzoneAction = targetDropzone.dataset.dropzoneAction

                // Get origin dropzone elements
                const originDropzone = draggableTask.closest(".dropzone")
                const oringinDropzoneId = originDropzone.getAttribute('id')
                const originDropzoneTaskContainer = originDropzone.querySelector(
                    `#${taskGroupIdPrefix}${oringinDropzoneId}`
                )
                const originDropzoneNumElement = originDropzone.querySelector(
                    `#${oringinDropzoneId}-task-num`
                )

                // move dragged element to the selected drop target
                originDropzoneTaskContainer.removeChild(draggableTask)
                targetDropzoneTaskContainer.appendChild(draggableTask)

                // Restore border styles to default
                targetDropzone.classList.remove(DRAGENTER_BORDER_STYLE)

                // Update the number of tasks
                setTaskNumString(
                    targetDropzonetaskNumElement,
                    targetDropzone.querySelector(`#${targetDropzoneId}-task-text`),
                    "increment",
                )
                setTaskNumString(
                    originDropzoneNumElement as HTMLElement,
                    originDropzone.querySelector(`#${oringinDropzoneId}-task-text`) as HTMLElement,
                    "decrement",
                )


                // Update the task status on DB
                const csrftoken = getCSRFToken()

                if(!csrftoken){
                    console.error("CSRF token not found")
                    return
                }
                const formData = new FormData();
                formData.append("event", targetDropzoneAction)
                // Important add / to the end of url, see
                // Because django can do redirect while mantaining the POST data
                const taskPk = draggableTask.dataset.taskPk
                await fetch(`/student/change_task_state/${taskPk}/`, {
                    method: "POST",
                    body: formData,
                    headers: {
                        'X-CSRFToken': csrftoken
                    },
                })

            }
        })
    })
})
