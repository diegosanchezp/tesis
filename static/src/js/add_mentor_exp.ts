import htmx from 'htmx.org';
import Alpine from "alpinejs"

import {startAlpine} from 'js/utils/alpine';

document.body.addEventListener("formset_validated", function(evt){
    // console.log(evt.detail.form_dict);
    // Update localstorage
    // localStorage.setItem('mentor_exp', JSON.stringify(evt.detail.form_dict));

    console.log(evt.detail)

    // The if prevents resetting the local storage key when forms are invalid
    if (evt.detail.cleaned_data){
        localStorage.setItem('mentor_cleaned_data', JSON.stringify(evt.detail.cleaned_data));
    }

    // If the action is validate, and the for is valid then perform a client side redirect
    if (evt.detail.action === "validate"){
        if(evt.detail.form_valid){
            window.location.href = evt.detail.next_url;
        }
    }
})


// Todo
// Cuando se carge la página, evento: DOM content loaded
// realizar una solicitud con la data guardada en localstorge
document.addEventListener("DOMContentLoaded", (event) => {
    const storage_key = "mentor_cleaned_data";
    const raw_exp = localStorage.getItem(storage_key);
    const mentor_exp = JSON.parse(raw_exp)
    if (mentor_exp.length > 0) {
        console.log(mentor_exp);
        // Realizar la solicitud
        htmx.ajax("GET","", {
            values: {
                "mentor_exp": raw_exp,
                "action": "get_form_localstorage",
                "carrer": localStorage.getItem(""),
            },
            target: "#formset",
            swap: "outerHTML",
        }).then(() =>{
            console.log('Content inserted successfully!');
        })
    }
});


const form_component = (form_prefix: string) => ({

    // The selected from localstorage
    profile: Alpine.$persist("").as("profile"),

    // The selected carrer from localstorage
    carreer: Alpine.$persist('').as('carreer'),

    // The selected interest themes
    interests: Alpine.$persist<string[]>([]).as("themes"),

    // Form data
    forms: Alpine.$persist<string[]>([]).as("mentor_cleaned_data"),
    form_prefix: form_prefix,

    init(){
        console.log(this.carreer)
        console.log(this.forms)
        console.log(this.form_prefix)
    },
    remove_subform(id: string, index: number){

        // Use -1 because the index is 1 based
        this.forms = this.forms.filter((value, i) => i !== index - 1);
        document.getElementById(id)?.remove();

        const totalFormInput = document.getElementById(`id_${this.form_prefix}-TOTAL_FORMS`);

        if (totalFormInput !== null) {
            const TOTAL_FORMS = parseInt(totalFormInput.getAttribute('value'))
            totalFormInput.setAttribute('value', `${TOTAL_FORMS - 1}`)
        }
    },
    get can_go_next_step(){
        return this.forms.length > 0;
    },
    /**Returns the url of the next page */
    get next_url(){
        return "todo"
    },

    /**validates with the server the form */
    validate_form(){
        // Get the form data
        const form = document.getElementById("formset") as HTMLFormElement;

        if(!form){
            console.log("could not get form")
            return
        }

        if(!form.checkValidity()){
            console.log("form is not valid")
            return
        }

        const formData = new FormData(form);

        formData.append("action", "validate")

        htmx.ajax("POST","", {
            values: Object.fromEntries(formData),
            target: "#formset",
            swap: "outerHTML",
        }).then(()=>{
            console.log("form validated")
        })
    }
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
