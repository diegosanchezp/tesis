import {AlpineComponent} from "alpinejs"
import {startAlpine} from 'js/utils/alpine';

interface FormData {
    first_name: string
    username: string
    email: string
    password1: string
    password2: string
    description: string
    web_page: string
}

interface IFormComponent extends FormData {
}

const form_component = (): AlpineComponent<IFormComponent> => ({
    first_name: Alpine.$persist("").as("busines:register:first_name"),
    username: Alpine.$persist("").as("busines:register:username"),
    email: Alpine.$persist("").as("busines:register:email"),
    password1: Alpine.$persist("").as("busines:register:password1"),
    password2: Alpine.$persist("").as("busines:register:password2"),
    description: Alpine.$persist("").as("busines:register:description"),
    web_page: Alpine.$persist("").as("busines:register:web_page"),
})

startAlpine(
    {
        stores:[],
        components: [
            {
                name: "form_component",
                component: form_component,
            }
        ]
    }
)
