import { myAlpineComponent, startAlpine } from "js/utils/alpine"

const ratingsComponent: myAlpineComponent = {
    name: "ratings",
    component: (rating: number | null) => ({
        current_rating: rating,
        init(){
        },
        setSelected: {
            ["@setGlobalRating"](e){
                this.current_rating = e.detail.value
                console.log(this.current_rating)
            }
        }
    }),
}

const machine = {
    selected: {
        click: "unselected",
    },
    unselected: {
        click: "selected",
    }
}
const ratingComponent: myAlpineComponent = {
    name: "rating",
    component: (rating: number, state: string = "unselected", current_rating: number = 0) => ({
        rating: rating,
        current_rating: current_rating,
        state: state,
        init(){
        },
        handleSelects: {
            ['@setGlobalRating.window'](e){
                // TODO find out why this log is printing 15 times
                this.current_rating = e.detail.value
            },
            ['@transition.window'](e){
                // We have already selected ourselves, don't do anything
                if(e.detail.index !== this.rating){
                    return
                }
                this.state = machine[this.state][e.detail.event]
            },
            ['@click'](){
                if (this.state === "unselected") {
                    if(1 < this.rating ){
                        // Paint all unselected from the current rating up to myself
                        if(this.current_rating < this.rating){
                            for (let i = this.current_rating + 1; i <= this.rating; i++) {
                                this.$dispatch('transition', {index: i, event: "click"})
                            }
                        }else{
                            // Paint all unselected up to myself
                            for(let i = 1; i <= this.rating; i++){
                                this.$dispatch('transition', {index: i, event: "click"})
                            }
                        }

                    }
                    // Paint myself, by transitioning to the next state
                    this.$dispatch('setGlobalRating', {value: this.rating})
                    return
                }

                if (this.state === "selected") {
                    // Unpaint those who are selected
                    if (this.rating < this.current_rating){
                        for(let i = this.rating + 1; i <= this.current_rating; i++){
                            this.$dispatch('transition', {index: i, event: "click"})
                        }
                        this.$dispatch('setGlobalRating', {value: this.rating})
                    }
                    return
                }
            },
        },
    }),
}

// Register component
startAlpine({
    components: [
        ratingsComponent,
        ratingComponent,
    ],
    stores: [
    ]
})

document.addEventListener("DOMContentLoaded", ()=>{
    const add_exp_ad = document.getElementById("advertisement-add-exp")
    const add_exp_btn = document.getElementById("add-exp-btn")
    if(add_exp_btn && add_exp_ad){
        add_exp_btn.addEventListener("click", (e)=>{
            add_exp_ad.remove()
        })
    }
})
document.addEventListener("htmx:afterRequest",(evt)=>{
    const target_id = evt.detail.target.id
    if(["my-exp-editing", "edit-or-add-experience"].includes(target_id)){
        // Alpine.start()
    }
})

