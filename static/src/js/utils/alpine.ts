import Alpine from "alpinejs"
import persist from '@alpinejs/persist'

export type myAlpineComponent = {
    name: string, component: () => any
}

export type myAlpineStore = {
    name: string
    store: any
    persist: boolean
    as: string
    persist_value: string
}


export type startAlpineParams = {
    components: myAlpineComponent[]
    stores: myAlpineStore[]
}

export function startAlpine(params: startAlpineParams){
    // Init stores

    // It is important that this line is here otherwise $persist property
    // wont be defined in the Alpine global object
    Alpine.plugin(persist)

    for (const store of params.stores){
        if (store.persist){
            Alpine.store(
                store.name,
                store.store(
                    {
                        [store.persist_value]: Alpine.$persist(store.persist_value).as(store.as)
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
