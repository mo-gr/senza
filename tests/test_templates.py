import click
from unittest.mock import MagicMock
from senza.templates._helper import get_iam_role_policy, get_mint_bucket_name, check_value


def test_template_helper_get_mint_bucket_name(monkeypatch):
    iam = MagicMock()
    iam.list_roles.return_value = {'list_roles_response': {'list_roles_result': {'is_truncated': 'false', 'roles': [
        {'arn': 'arn:aws:iam::123:role/app-delivery'}]}}}
    iam.get_account_alias.return_value = {
        'list_account_aliases_response': {'list_account_aliases_result': {'account_aliases': ['myorg-foobar']}}
    }
    monkeypatch.setattr('boto.iam.connect_to_region', MagicMock(return_value=iam))
    s3 = MagicMock()
    s3.return_value.Bucket.return_value.name = 'myorg-stups-mint-123-myregion'
    monkeypatch.setattr('boto3.resource', s3)

    assert 'myorg-stups-mint-123-myregion' == get_mint_bucket_name('myregion'), 'Find Mint Bucket'

    s3 = MagicMock()
    s3.return_value.Bucket.return_value.load.side_effect = Exception()
    monkeypatch.setattr('boto3.resource', s3)
    assert('myorg-stups-mint-123-otherregion' == get_mint_bucket_name('otherregion'),
           'Return Name of Bucket, if no other Bucket found')

    exist_bucket = MagicMock()
    exist_bucket.name = 'myorg-stups-mint-123-myregion'
    s3 = MagicMock()
    s3.return_value.Bucket.return_value.load.side_effect = Exception()
    s3.return_value.buckets.all.return_value = [exist_bucket]
    monkeypatch.setattr('boto3.resource', s3)
    assert 'myorg-stups-mint-123-myregion' == get_mint_bucket_name('otherregion'), 'Find Mint bucket in other Region'


def test_template_helper_get_iam_role_policy(monkeypatch):
    expected_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowMintRead",
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject"
                ],
                "Resource": [
                    "arn:aws:s3:::bucket-name/myapp/*"
                ]
            },
        ]
    }

    assert expected_policy == get_iam_role_policy('myapp', 'bucket-name', 'myregion')


def test_template_helper_check_value():
    f = check_value(5, '^[A-Z]+$')
    assert 'ABC' == f('ABC')
    try:
        f('abc')
    except click.UsageError:
        pass
    except:
        assert False, 'check_value raise with a unkown exception'
    else:
        assert False, 'check_value doesnot return with a raise'

    try:
        f('ABCABC')
    except click.UsageError:
        pass
    except:
        assert False, 'check_value raise with a unkown exception'
    else:
        assert False, 'check_value doesnot return with a raise'
