#include "MyComponent.h"

#include "nau/scene/scene_manager.h"
#include "nau/service/service_provider.h"
#include "nau/input.h"
#include "nau/scene/components/directional_light_component.h"
#include "nau/math/math.h"
#include <EASTL/algorithm.h>

NAU_IMPLEMENT_DYNAMIC_OBJECT(MyComponent)

void MyComponent::updateComponent(float dt)
{
	bool inPlaymode = !nau::getServiceProvider().get<nau::scene::ISceneManager>().getDefaultWorld().isSimulationPaused();
	auto* light = getParentObject().getAllComponents<nau::scene::DirectionalLightComponent>()[0]->as<nau::scene::DirectionalLightComponent*>();
	if (light && inPlaymode)
	{
		const float ROT_STEP = 0.1f;
		const float AMPLITUDE = 60.0f;
		if (nau::input::isMouseButtonHold(0, nau::input::MouseKey::Button0))
			m_degrees += ROT_STEP;
		else if (nau::input::isMouseButtonHold(0, nau::input::MouseKey::Button2))
			m_degrees -= ROT_STEP;
		
		m_degrees = eastl::clamp(m_degrees, -AMPLITUDE, AMPLITUDE);

		getParentObject().setRotation(nau::math::quat::rotationZ(m_degrees));
		light->setColor({ 1.0f, m_degrees / AMPLITUDE, 1.0f });
	}
}
