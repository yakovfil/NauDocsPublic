#pragma once

#include "nau/scene/components/component.h"
#include "nau/scene/components/component_life_cycle.h"
#include "nau/scene/scene_object.h"

class MyComponent final : public nau::scene::Component,
                          public nau::scene::IComponentUpdate
{
    NAU_OBJECT(MyComponent, nau::scene::Component, nau::scene::IComponentUpdate)
    NAU_DECLARE_DYNAMIC_OBJECT

    NAU_CLASS_FIELDS(
        CLASS_NAMED_FIELD(m_field, "field"),
    )

    void updateComponent(float dt) override;

private:
    float m_field = 1.0f;
};
