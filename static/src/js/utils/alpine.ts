import Alpine from "alpinejs"
// plugins
import persist from '@alpinejs/persist'
// htmx, do not change the order of these imports
// https://github.com/bigskysoftware/htmx/issues/1690#issue-1844615295
import 'js/htmx';
// .js has to be added otherwise import error is raised
import 'htmx.org/dist/ext/alpine-morph.js'
 
export type myAlpineComponent = {
    name: string, component: () => any
}

export type myAlpineStore = {
    name: string
    store: any
    persist: boolean
    as: string
    persist_value: string
    persist_prop: string
}


export type startAlpineParams = {
    components: myAlpineComponent[]
    stores: myAlpineStore[]
}

export function startAlpine(params: startAlpineParams){
    window.Alpine = Alpine
    // It is important that this line is here otherwise $persist property
    // wont be defined in the Alpine global object
    Alpine.plugin(persist)

    // Init stores
    for (const store of params.stores){
        if (store.persist){
            Alpine.store(
                store.name,
                store.store(
                    {
                        [store.persist_prop]: Alpine.$persist(store.persist_value).as(store.as)
                    }
                )
            )
        }else{
            Alpine.store(store.name, store.store())
        }
    }

    for (const component of params.components){
        Alpine.data(component.name, component.component)
    }

    // Init components

    Alpine.start()
}
