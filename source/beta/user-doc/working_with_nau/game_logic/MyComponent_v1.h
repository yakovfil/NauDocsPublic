#pragma once

#include "nau/scene/components/component.h"
#include "nau/scene/components/component_life_cycle.h"
#include "nau/scene/scene_object.h"

class MyComponent final : public nau::scene::Component,
                          public nau::scene::IComponentUpdate
{
    NAU_OBJECT(MyComponent, nau::scene::Component, nau::scene::IComponentUpdate)
    NAU_DECLARE_DYNAMIC_OBJECT

    void updateComponent(float dt) override;
};
