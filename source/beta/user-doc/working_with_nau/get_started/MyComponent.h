#pragma once
#include "nau/scene/components/component.h"
#include "nau/scene/components/component_life_cycle.h"
#include "nau/scene/scene_object.h"
#include "nau/physics/components/rigid_body_component.h"

class MyComponent final : public nau::scene::Component,
    public nau::scene::IComponentUpdate
{
    NAU_OBJECT(MyComponent, nau::scene::Component, nau::scene::IComponentUpdate)
        NAU_DECLARE_DYNAMIC_OBJECT

        void updateComponent(float dt) override;

public:


private:
    float m_degrees = 0.0f;

};
