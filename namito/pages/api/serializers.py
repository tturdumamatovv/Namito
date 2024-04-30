from rest_framework import serializers

from namito.pages.models import MainPageSlider, MainPage, StaticPage



class MainPageSliderSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = MainPageSlider
        fields = ['title', 'description', 'image', 'link']

    def get_image(self, slider):
        if slider.image and slider.image.file:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(slider.image.url)
            else:
                return slider.image.url
        return None


class MainPageSerializer(serializers.ModelSerializer):
    slider = serializers.SerializerMethodField()

    class Meta:
        model = MainPage
        fields = ['banner1', 'banner2', 'banner3', 'title', 'description', 'counter1_title',
                  'counter1_value', 'counter2_title', 'counter2_value', 'counter3_title',
                  'counter3_value', 'button_link', 'button', 'slider']

    def get_slider(self, page):
        slider_qs = MainPageSlider.objects.filter(page=page)
        return MainPageSliderSerializer(slider_qs, many=True, context=self.context).data


class StaticPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaticPage
        fields = ['title', 'slug', 'content', 'image', 'meta_title',
                  'meta_description', 'created_at', 'updated_at']
