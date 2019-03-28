import pytest

from ai.backend.client.exceptions import BackendAPIError
from ai.backend.client.session import Session


@pytest.mark.asyncio
@pytest.mark.integration
class TestImage:

    async def test_list_images_by_admin(self):
        with Session() as sess:
            images = sess.Image.list()
            image = images[0]
        assert len(images) > 0
        assert 'name' in image
        assert 'tag' in image
        assert 'hash' in image

    async def test_list_images_by_user(self, userconfig):
        with Session() as sess:
            images = sess.Image.list()
            image = images[0]
        assert len(images) > 0
        assert 'name' in image
        assert 'tag' in image
        assert 'hash' in image

    # This is invasive...
    # async def test_rescan_images(self):
    #     pass

    async def test_alias_dealias_image_by_admin(self):
        with Session() as sess:
            def get_test_aliases():
                items = sess.Image.list(fields=('name', 'tag', 'aliases'))
                for item in items:
                    if 'lua' in item['name'] and '5.1-alpine3.8' in item['tag']:
                        return item['aliases']

            test_alias = 'testalias-b9f1ce136f584ca892d5fef3e78dd11d'
            sess.Image.aliasImage(test_alias, 'lua:5.1-alpine3.8')
            assert get_test_aliases() == [test_alias]

            sess.Image.dealiasImage(test_alias)
            assert len(get_test_aliases()) == 0

    async def test_user_cannot_mutate_alias_dealias(self, userconfig):
        with Session() as sess:
            test_alias = 'testalias-b9f1ce136f584ca892d5fef3e78dd11d'
            with pytest.raises(BackendAPIError):
                sess.Image.aliasImage(test_alias, 'lua:5.1-alpine3.8')
            with pytest.raises(BackendAPIError):
                sess.Image.dealiasImage(test_alias)
